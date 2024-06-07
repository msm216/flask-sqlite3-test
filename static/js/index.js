// Add User: openModal(null, null, 'add')
// Edit: openModal(1, 'Alice', 'edit')
function openUserModal(id, name, registered_date, group_id, mode) {
    // 设置隐藏字段
    // 如果 || 左边对象为真值则以左边对象赋值，假值则用右边对象
    // 假值包括：false，0，-0，0n，null，""，undefined，NaN
    document.getElementById('userId').value = id;
    document.getElementById('userName').value = name || '';
    document.getElementById('userGroupID').value = group_id || 0;
    document.getElementById('userRegisteredOn').value = registered_date || '';
    // 影响模态框submit功能
    document.getElementById('userModalMode').value = mode;
    // 动态调整模态框标题和按钮文本
    // 三元运算符 variable = condition ? A : B
    // 如果 condition 满足（mode === 'add'）则赋值为 A 否则 B
    document.getElementById('userModalTitle').innerText = mode === 'add' ? 'Add User' : 'Edit User';
    document.getElementById('userModalSubmitButton').innerText = mode === 'add' ? 'Add User' : 'Save Changes';
    // 显示模态框
    document.getElementById('userModal').classList.add('is-active');
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function deleteUser(id) {
    confirmAction('Are you sure you want to delete this user?', function() {
        fetch('/delete_user/' + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    });
}

function openGroupModal(id, name, created_date, mode) {
    ////////////////
    console.log('Data to template:');
    console.log('id:', id);
    console.log('name:', name);
    console.log('created_date:', created_date, 'of type: ', typeof created_date);
    console.log('mode:', mode);
    ////////////////
    // 设置隐藏字段
    // 如果 || 左边对象为真值则以左边对象赋值，假值则用右边对象
    // 假值包括：false，0，-0，0n，null，""，undefined，NaN
    document.getElementById('groupId').value = id;
    document.getElementById('groupName').value = name || '';
    document.getElementById('groupCreatedOn').value = created_date || '';
    // 影响模态框submit功能
    document.getElementById('groupModalMode').value = mode;
    // 动态调整模态框标题和按钮文本
    // 三元运算符 variable = condition ? A : B
    // 如果 condition 满足（mode === 'add'）则赋值为 A 否则 B
    document.getElementById('groupModalTitle').innerText = mode === 'add' ? 'Add Group' : 'Edit Group';
    document.getElementById('groupModalSubmitButton').innerText = mode === 'add' ? 'Add Group' : 'Save Changes';
    // 显示模态框
    document.getElementById('groupModal').classList.add('is-active');
}

function deleteGroup(id) {
    confirmAction('Are you sure you want to delete this group?', function() {
        fetch('/delete_group/' + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    });
}