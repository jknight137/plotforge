import git

def init_git_repo(project_path):
    repo = git.Repo.init(project_path)
    repo.git.add(A=True)
    repo.index.commit("Initial commit: Project created.")
