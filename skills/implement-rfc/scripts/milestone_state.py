"""Repository identity shared by primary checkpoints and coordinated handoffs."""
def repository_state(context):
    """Local handoff identity; personal callers store it under runtime_root."""
    import subprocess
    import project_config
    def git(root, *args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True,
                                       env=project_config.git_environment()).strip()
    return {
        'source_root': str(context.source_root), 'workflow_root': str(context.workflow_root),
        'source_common_dir': str(context.source_common_dir),
        'workflow_common_dir': str(context.workflow_common_dir),
        'source_branch': git(context.source_root, 'branch', '--show-current'),
        'source_revision': git(context.source_root, 'rev-parse', 'HEAD'),
        'workflow_branch': git(context.workflow_root, 'branch', '--show-current'),
        'workflow_revision': git(context.workflow_root, 'rev-parse', 'HEAD'),
    }

