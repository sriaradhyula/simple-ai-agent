FROM langchain/langgraph-api:3.11



# -- Installing local requirements --
ADD requirements.txt /deps/__outer_simple-ai-agent/src/requirements.txt
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -r /deps/__outer_simple-ai-agent/src/requirements.txt
# -- End of local requirements install --

# -- Adding non-package dependency simple-ai-agent --
ADD . /deps/__outer_simple-ai-agent/src
RUN set -ex && \
    for line in '[project]' \
                'name = "simple-ai-agent"' \
                'version = "0.1"' \
                '[tool.setuptools.package-data]' \
                '"*" = ["**/*"]'; do \
        echo "$line" >> /deps/__outer_simple-ai-agent/pyproject.toml; \
    done
# -- End of non-package dependency simple-ai-agent --

# -- Installing all local dependencies --
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*
# -- End of local dependencies install --
ENV LANGSERVE_GRAPHS='{"simple-devops-agent": "/deps/__outer_simple-ai-agent/src/simple_ai_agent.py:get_graph"}'

WORKDIR /deps/__outer_simple-ai-agent/src