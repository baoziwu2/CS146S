具体的代码在仓库里，这里一两句讲解法
### chain_of_thought.py
按照零样本 CoT 处理即可

### k_shot_prompting.py
~~关键是把样例答案写上去~~
小模型处理这个是真没招
### rag.py
rag 的重点就是强调模型严格按照 context 内容来（毕竟出幻觉了啥都查不到）
不过本题返回空 context 也可能通过，因为验证 API 格式很通用（负负得正这一块）
### reflexion.py
向反思模型说明提供内容和修改建议的格式即可，另外由于反思模型要负责评估，所以把规则写进上下文会好一些
### self_consistency_prompting.py
防止偶然的出错所以多次运行取众数
如果取不出众数说明可能超过了当前提示词或模型的能力边界

### tool_calling.py
和 RAG 要注意的基本一样（我说 RAG 就是一种工具调用有没有懂的）
让模型返回精确的 json 即可