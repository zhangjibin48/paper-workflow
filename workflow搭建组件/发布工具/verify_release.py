"""Verify package references and real isolated installation/replacement behavior."""
import hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
from urllib.parse import unquote
from install import PACKAGE,verify

def main():
    manifest=verify()
    for item in manifest['files']:
        path=PACKAGE/item['path']
        text=path.read_text(encoding='utf-8')
        assert not re.search(r'\b[A-Za-z]:[\\/]|@gmail|sk-[A-Za-z0-9]{12,}',text),path
        # The package uses Markdown inline links, with snippets fenced out.
        plain=re.sub(r'```.*?```','',text,flags=re.S)
        for link in re.findall(r'\]\(([^)]+)\)',plain):
            link=link.strip('<>').split('#',1)[0]
            if not link or re.match(r'^[a-z]+:',link):
                continue
            target=(path.parent/unquote(link)).resolve()
            assert target.is_relative_to(PACKAGE.resolve()) and target.exists(),(path,link)
    scripts=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='paper-workflow-release-') as temp:
        root=Path(temp)
        dsh=root/'dsh'
        command=[sys.executable,str(scripts/'install.py'),'--dsh-home',str(dsh)]
        subprocess.run(command,check=True,capture_output=True)
        receipt=json.loads((dsh/'integrations/paper-workflow/installation.json').read_text(encoding='utf-8'))
        assert len(receipt['entries'])==10
        release=Path(receipt['release'])
        verify(release)
        entries={p:Path(p).read_bytes() for p in (x['entry'] for x in receipt['entries'])}
        blocked=subprocess.run(command,capture_output=True)
        assert blocked.returncode!=0 and all(Path(p).read_bytes()==v for p,v in entries.items())
        subprocess.run(command+['--replace'],check=True,capture_output=True)
        replaced=json.loads((dsh/'integrations/paper-workflow/installation.json').read_text(encoding='utf-8'))
        assert all(Path(x['previous']).read_bytes()==entries[x['entry']] for x in replaced['entries'])
        workspace=root/'workspace'
        init=[sys.executable,str(scripts/'init_workspace.py'),'--workspace',str(workspace),'--vault',str(root/'vault')]
        subprocess.run(init,check=True,capture_output=True)
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in workspace.rglob('*') if p.is_file()}
        assert '尚未开始' in (workspace/'当前任务.md').read_text(encoding='utf-8')
        assert '任务标识：无' in (workspace/'当前任务.md').read_text(encoding='utf-8')
        assert '当前任务临时限制：无' in (workspace/'行为规则.md').read_text(encoding='utf-8')
        assert subprocess.run(init,capture_output=True).returncode!=0
        assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items())
    print(f'Passed: {len(manifest["files"])} hashes and local links; install, conflict protection, backup/replace, empty workspace, no overwrite.')

if __name__=='__main__':
    main()
