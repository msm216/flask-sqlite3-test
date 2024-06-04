function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function closeUserModal() {
    document.getElementById('userModal').classList.remove('is-active');
}

function submitUser() {
    var id = document.getElementById('userId').value;
    var name = document.getElementById('userName').value;
    var group_id = document.getElementById('userGroup').value;
    var mode = document.getElementById('userModalMode').value;
    // 根据 mode 条件赋值 url
    var url
    switch (mode) {
        case 'add':
            url = '/add';
            break;
        case 'edit':
            url = '/edit/' + id;
            break;
        default:
            // 未知模式直接返回
            console.error('Unknown mode:', mode);
            return;
    }
    var data = {
        name: name,
        group_id: group_id
    };
    confirmAction('Are you sure you want to ' + (mode === 'add' ? 'add this user?' : 'edit this user?'), function() {
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