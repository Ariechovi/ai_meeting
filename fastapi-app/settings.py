TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "111.230.199.27",
                "port": 3306,
                # 数据库名称
                "database": "ai_meeting",
                "user": "root",
                # 数据库密码
                "password": "df123456",
                "minsize": 1,
                "maxsize": 10,
                "charset": "utf8mb4",
                "echo": True
            }
        },
    },
    "apps": {
      "models": {
          "models": ["models"],
          "default_connection": "default",
      }
    },
    # 是否使用时区
    "use_tz": True,
    "timezone": "Asia/Shanghai"
}

JWT_SECRET = "ai-meeting-jwt-secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

