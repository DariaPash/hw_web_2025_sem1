def sidebar_data(request):
    """Контекстный процессор для данных сайдбара (теги и лучшие пользователи)"""
    fake_tags = [
        {'name': 'python'},
        {'name': 'javascript'},
        {'name': 'django'},
        {'name': 'html'},
        {'name': 'css'},
        {'name': 'mysql'},
        {'name': 'php'},
        {'name': 'java'},
        {'name': 'c++'},
        {'name': 'react'},
    ]
    
    fake_users = [
        {'username': 'john_doe', 'reputation': 156, 'initial': 'J'},
        {'username': 'jane_smith', 'reputation': 142, 'initial': 'J'},
        {'username': 'alex_dev', 'reputation': 98, 'initial': 'A'},
        {'username': 'maria_coder', 'reputation': 87, 'initial': 'M'},
    ]
    
    return {
        'popular_tags': fake_tags,
        'best_users': fake_users,
    }

