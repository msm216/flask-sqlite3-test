
function closeUserModal() {
    document.getElementById('userModal').classList.remove('is-active');
}

function submitUser() {
    var id = document.getElementById('userId').value;
    var name = document.getElementById('userName').value;
    var group_id = document.getElementById('userGroupID').value || 0;
    // 如果获取 'userRegisteredOn' 的为空值（包括''）则以当天日期赋值
    var registered_on = document.getElementById('userRegisteredOn').value || new Date().toISOString().split('T')[0];
    var mode = document.getElementById('userModalMode').value;
    // 根据 mode 条件赋值 url
    var url
    switch (mode) {
        case 'add':
            url = '/add_user';
            break;
        case 'edit':
            url = '/edit_user/' + id;
            break;
        default:
            // 未知模式直接返回
            console.error('Unknown mode:', mode);
            return;
    }
    ////////////////
    console.log('Submitting data:')
    console.log('id: ', id)
    console.log('name: ', name)
    console.log('registered_on:', registered_on, 'of type: ', typeof registered_on);
    console.log('group_id:', group_id, 'of type: ', typeof created_on);
    console.log('mode: ', mode)
    ////////////////
    var data = {
        name: name,
        registered_on: registered_on,
        group_id: group_id
    };
    confirmAction('Are you sure you want to ' + (mode === 'add' ? 'add this user?' : 'modify this user?'), function() {
        // 发送请求
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    });
}