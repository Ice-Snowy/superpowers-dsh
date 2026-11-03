# superpowers-dsh
修改自原来的superpowers，大部分移值，部分脚本采用python.


未移植 / 降级项

  项目                                      	状态  	原因与替代                                   
  brainstorming/scripts/start-server.sh、stop-server.sh	未移植 	依赖 bash 后台进程，且原实现检测到 Windows 会切前台阻塞。Windows 下建议用文字版头脑风暴
  systematic-debugging/find-polluter.sh   	未移植 	同上；需要二分定位时可改用 Python 手写等价脚本             
  hooks/session-start                     	不适用 	DSH 没有 hooks 机制（/hooks 仅为占位说明）。替代：在项目 AGENTS.md 里声明"每次会话先加载 using-superpowers"
  gh CLI（diagnosing-superpowers）          	未安装 	该技能已内置降级路径：无 gh 时用 curl 调 API，或直接给出网页链接 
  subagent_type（如 general-purpose、只读子代理）  	不支持 	DSH 的 subagent 只有 prompt，没有类型参数。角色由技能自带的提示词模板表达（implementer-prompt.md 等）；"只读"只能靠提示词约束 + 事后审查
  插件清单（.claude-plugin/、.codex-plugin/ 等）  	不需要 	DSH 靠扫描技能根目录发现技能，不用清单                   
  docs/superpowers/plans\|specs/ 路径       	保持原样	与宿主无关                                   


