FROM codercom/code-server:latest

LABEL ai-coach="true" \
      description="AI Coach 开发环境镜像"

USER root

# 安装 Python 3.12
# RUN apt-get update && apt-get install -y python3 python3-pip
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update --fix-missing && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean

# 安装 Node.js 22.14.0
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    node --version && \
    npm --version

# 创建工作目录
RUN mkdir -p /home/coder/project
WORKDIR /home/coder/project

# 权限修复
RUN chown -R coder:coder /home/coder

# 给 coder 用户 root 权限codesandbox-image
RUN apt-get install -y sudo && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER coder

# 启动 code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none"]
