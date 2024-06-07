
function closeGroupModal() {
    document.getElementById('groupModal').classList.remove('is-active');
}

function submitGroup() {
    var id = document.getElementById('groupId').value;
    var name = 'Group ' + document.getElementById('groupName').value;
    // 如果获取 'groupCreatedOn' 的为空值（包括''）则以当天日期赋值
    var created_on = document.getElementById('groupCreatedOn').value || new Date().toISOString().split('T')[0];
    var mode = document.getElementById('groupModalMode').value;
    // 根据 mode 条件赋值 url
    var url
    switch (mode) {
        case 'add':
            url = '/add_group';
            break;
        case 'edit':
            url = '/edit_group/' + id;
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
    console.log('created_date:', created_on, 'of type: ', typeof created_on);
    console.log('mode: ', mode)
    ////////////////
    var data = {
        name: name,
        created_on: created_on
    };
 
    confirmAction('Are you sure you want to ' + (mode === 'add' ? 'add this group?' : 'modify this group?'), function() {
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