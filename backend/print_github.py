from app.core.config import settings

private_key = settings.GITHUB_PRIVATE_KEY.replace("\\n", "\n")

print(private_key[:200])