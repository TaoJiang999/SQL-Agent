# ============================================
# SQL Agent MySQL 沙盒数据库
# ============================================
FROM mysql:8.0

# 设置环境变量
ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=ecommerce
ENV MYSQL_USER=sandbox_user
ENV MYSQL_PASSWORD=sandbox_password

# 设置字符集
ENV LANG=C.UTF-8

# 配置MySQL
COPY my.cnf /etc/mysql/conf.d/custom.cnf

# 复制初始化脚本
COPY init/ /docker-entrypoint-initdb.d/

# 暴露端口
EXPOSE 3306

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1
