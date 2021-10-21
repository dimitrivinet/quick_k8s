from typing import Dict

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "admin",
        "email": "admin@devinci.fr",
        "hashed_password": "$2b$12$MyslprgxZf7F0XqgCS9xmuaSn2IJcv56M.ZhOMWWLOUpacHm406D2",
        "disabled": False,
    },
    "user_level1": {
        "username": "user_level1",
        "full_name": "user_level1",
        "email": "user_level1@devinci.fr",
        "hashed_password": "$2b$12$Q94uH2liW4Grp9hK87FtdunZ0m8m4Vs3SLevNLG6./mA24AIYftPG",
        "disabled": False,
    },
    "user_level2": {
        "username": "user_level2",
        "full_name": "user_level2",
        "email": "user_level2@devinci.fr",
        "hashed_password": "$2b$12$9iuS43DDsBiaCwcDAKtO2uRrWcUrAnZSWQFN3G9NxGzZd2SIBfFPy",
        "disabled": True,
    },
}

user_deployments: Dict[str, list] = {}
