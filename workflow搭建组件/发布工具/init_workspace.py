"""Create a new empty paper workspace. Existing files are never overwritten."""
import argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--vault',type=Path,required=True)
    args=p.parse_args()
    workspace=args.workspace.expanduser().resolve()
    vault=args.vault.expanduser().resolve()
    if workspace==vault or workspace.is_relative_to(vault) or vault.is_relative_to(workspace):
        raise ValueError('Use separate, non-nested workspace and vault directories')
    if workspace.exists() and any(workspace.iterdir()):
        raise FileExistsError('Choose an empty workspace; existing data is preserved')
    documents={
        'AGENTS.md':f'''# 正式论文工作区

本目录为正式状态目录，归档回执在 `归档记录/`。每次开始用 paper-align-state 读取学习档案、当前任务、最新行为规则及适用索引。实际论文由当前任务和用户最新请求确定。变化由 paper-update-state 保存并回读；原话／正文→索引→当前入口分别完成，不用摘要替代正文。

八个阶段逐一由用户明确调用目标 Skill 并下令开始，完成当前阶段就停止等待；第六阶段两份 Skill 分别启动。当前阶段可内部使用对齐读取和日常保存，完成后只返回当前阶段。用户的想法、追问、“明白了”或已存下一步不授权切换；中间存档不启动正式归档。

第四阶段按已部署制图约定先看配套示例，再根据实际实验代码画 draw.io 中文横向全程图，训练与推理按实际分别画，再结合图、论文、公式和代码由整体到组件及关键参数学习，逐项核实全部核心创新。保存可编辑图与逐页核对的可读预览；缺代码或图不可读先报告缺口，不冒充已完成。

正式 Obsidian 库路径为 `{vault.as_posix()}`，调用工具时明确选择。Zotero 保存正式三笔记及选文记录，Obsidian 保存导航、写作素材与关系图。使用已部署工具 Skill；找文实际调用 Undermind MCP，PDF 按实际附件用本地 MinerU。未知身份、版本、用户理解保持未知；保留用户手改，结果不明先查真实对象再重试。
''',
        '学习档案.md':'''# 学习档案

- 版本：1
- 记录性质：正式数据
- 专业与学习基础：未知，按用户实际信息补充。
- 已读论文与已掌握范围：未知。
- 兴趣与研究范围：尚未指定。
- 投稿目标、期限与算力：未知。

用户自述、作者报告与 AI 候选分别记录。已有信息直接沿用，只询问影响下一步的缺项。
''',
        '行为规则.md':'''# 行为规则

- 版本：1
- 已启用长期个人规则：无。
- 候选规则：无。
- 当前任务临时限制：无。

通用业务约定从部署的 Skill 加载；长期个人纠正按实际原话、范围和来源保存。
''',
        '当前任务.md':'''# 当前任务

- 版本：1
- 状态：尚未开始
- 任务标识：无
- 当前论文：无
- 工作区索引：无
- 下一步：等待用户明确调用 paper-align-state 并下令开始第一阶段，再按其目标对齐。
''',
        '开始使用.md':'''# 开始使用

在 DeepSeek Harness 选择本目录并新建会话，输入“调用 paper-align-state，开始第一阶段”，再说明方向或 Zotero 中的论文题名。每个阶段完成后 Agent 停止等待；下一阶段由你明确调用对应 Skill 并下令开始。工具读取与日常保存可在当前阶段内部进行，记录供下次恢复。

保持 Zotero 与 Obsidian 可访问，解析 PDF 使用已配置的本地 MinerU。Undermind 在找文时按实际连接使用。第四阶段提供论文与实验代码，先用 draw.io 画完整流程图，再图文学习；有训练与推理时分别画。阅读深度、个人判断和理解依据你的真实回应。
'''}
    conflicts=[str(workspace/name) for name in documents if (workspace/name).exists()]
    if conflicts:
        raise FileExistsError('Choose an empty workspace. Existing files: '+', '.join(conflicts))
    workspace.mkdir(parents=True,exist_ok=True)
    vault.mkdir(parents=True,exist_ok=True)
    for name,text in documents.items():
        (workspace/name).write_text(text,encoding='utf-8',newline='\n')
    for name in ['任务成果','归档记录']:
        (workspace/name).mkdir(exist_ok=True)
    print(f'Created empty workspace: {workspace}; vault directory: {vault}')
    print('Open the vault directory in Obsidian. This script does not alter app permissions or accounts.')

if __name__=='__main__':
    main()
