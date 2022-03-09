from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="src",
    install_requires=[
        "fastapi==0.74.1",
        "psycopg2==2.9.3",
        "pydantic==1.9.0",
        "pytest==7.0.1",
        "python-dotenv==0.19.2",
        "python-multipart==0.0.5",
        "SQLAlchemy==1.4.31",
        "uvicorn==0.17.5",
    ],
)
