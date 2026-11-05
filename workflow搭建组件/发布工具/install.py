"""Install business skills from the portable package; never change model/security config."""
import argparse
from datetime import datetime
import hashlib,json,re,shutil
from pathlib import Path

PACKAGE=Path(__file__).resolve().parent.parent/'发布包'

def verify(package=PACKAGE):
    manifest=json.loads((package/'发布清单.json').read_text(encoding='utf-8'))
    for entry in manifest['files']:
        path=(package/entry['path']).resolve()
        if not path.is_relative_to(package.resolve()):
            raise ValueError('Package path escaped release directory')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError(f'Hash mismatch: {entry["path"]}')
    if len(manifest['skills'])!=10:
        raise ValueError('Expected ten business skills')
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dsh-home',type=Path,default=Path.home()/'.dsh')
    parser.add_argument('--check',action='store_true',help='Verify package only; writes nothing')
    parser.add_argument('--replace',action='store_true',help='Back up and replace existing paper-* discovery entries')
    args=parser.parse_args()
    manifest=verify()
    if args.check:
        print(f'Package OK: 10 business skills, {len(manifest["files"])} resources.')
        return
    dsh=args.dsh_home.expanduser().resolve()
    release=dsh/'integrations/paper-workflow/releases'/manifest['version']
    plans=[]
    for relative in manifest['skills']:
        source=PACKAGE/relative
        text=source.read_text(encoding='utf-8')
        match=re.match(r'\A---\n(.*?)\n---\n',text,re.S)
        if not match:
            raise ValueError(f'Missing frontmatter: {relative}')
        target=release/relative
        entry=dsh/'skills'/source.parent.name/'SKILL.md'
        if entry.exists() and not args.replace:
            raise FileExistsError(f'{entry}: use --replace to back up and replace')
        content=(match.group(0)+'\n# 论文工作流执行入口\n\n'
                 f'执行前完整读取 [阶段规则](<{target.as_posix()}>)，并按其中条件读取引用资源。'
                 '相对路径相对于被引用的发布文件所在目录解析。'
                 '实际状态目录与论文从当前工作区及用户请求取得。'
                 '用户明确调用并下令开始后才启动业务阶段；完成后停止等待。'
                 '当前阶段内部的对齐读取与日常保存按阶段控制约定返回调用方。\n')
        plans.append((entry,content))
    if release.exists():
        existing=json.loads((release/'发布清单.json').read_text(encoding='utf-8'))
        if existing!=manifest:
            raise FileExistsError('Same version already installed with different contents')
        verify(release)
    else:
        release.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(PACKAGE,release)
        verify(release)
    backup=dsh/'integrations/paper-workflow/backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    records=[]
    for entry,content in plans:
        previous=None
        if entry.exists():
            old=backup/entry.parent.name/'SKILL.md'
            old.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(entry,old)
            previous=str(old)
        entry.parent.mkdir(parents=True,exist_ok=True)
        entry.write_text(content,encoding='utf-8',newline='\n')
        assert entry.read_text(encoding='utf-8')==content
        records.append({'entry':str(entry),'previous':previous})
    receipt=dsh/'integrations/paper-workflow/installation.json'
    receipt.write_text(json.dumps({'version':manifest['version'],'release':str(release),'entries':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Installed ten business skill entries. Receipt: {receipt}')
    print('Tool adapters and account connections are configured separately; model/security settings unchanged.')

if __name__=='__main__':
    main()
