function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function closeGroupModal() {
    document.getElementById('groupModal').classList.remove('is-active');
}

function submitGroup() {
    var id = document.getElementById('groupId').value;
    var name = document.getElementById('groupName').value;
    var group_id = document.getElementById('groupGroup').value;
    var mode = document.getElementById('groupModalMode').value;
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
    };
    confirmAction('Are you sure you want to ' + (mode === 'add' ? 'add this group?' : 'edit this group?'), function() {
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