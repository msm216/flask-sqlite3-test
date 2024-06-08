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


// 将复选框值传递给表单
function appendCheckedCheckboxesToForm(formId, checkboxClass, hiddenInputName) {
    var form = document.getElementById(formId);
    var checkboxes = document.querySelectorAll(checkboxClass);
    checkboxes.forEach(function(checkbox) {
        if (checkbox.checked) {
            var hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = hiddenInputName;
            hiddenInput.value = checkbox.value;
            form.appendChild(hiddenInput);
        }
    });
}

// 为 userFilterForm 表单添加 submit 事件的监听器
document.getElementById('userFilterForm').addEventListener('submit', function(event) {
    // 调用分离的函数，将复选框值传递给表单
    appendCheckedCheckboxesToForm('userFilterForm', '.group-checkbox', 'group-select');
});

// 监听DOMContentLoaded事件，确保DOM完全加载和解析完成后再执行代码
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有下拉菜单的触发按钮
    var dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    // 为每个下拉菜单设置事件监听器，不互相影响
    dropdownToggles.forEach(function(dropdownToggle) {
        var dropdownMenu = dropdownToggle.nextElementSibling;
        dropdownToggle.addEventListener('click', function() {
            dropdownMenu.classList.toggle('show');
        });
        // 为文档添加click事件监听器，确保点击下拉菜单外部时隐藏菜单
        document.addEventListener('click', function(event) {
            if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    });
});

/*
// 为 userFilterForm 元素添加监听 submit 事件的监听器
document.getElementById('userFilterForm').addEventListener('submit', function(event) {
    // 选择所有 group-checkbox 类的复选框元素，并将它们存储在checkboxes变量中
    var checkboxes = document.querySelectorAll('.group-checkbox');
    // 遍历每一个选中的复选框，forEach 方法对 checkboxes 中的每一个元素执行传入的回调函数（回调函数在哪定义了？）
    checkboxes.forEach(function(checkbox) {
        // 检查当前遍历的复选框是否被选中（checked属性为true）
        if (checkbox.checked) {
            // 创建一个新的 input 元素
            var hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';    // 类型为隐藏
            hiddenInput.name = 'group_select';    // 名称为 group_select
            hiddenInput.value = checkbox.value;
            // 将创建的隐藏输入元素添加到表单中
            document.getElementById('userFilterForm').appendChild(hiddenInput);
        }
    });
});

// 监听DOMContentLoaded事件，这个事件在初始的HTML文档完全加载和解析完成后触发
document.addEventListener('DOMContentLoaded', function() {
    // 获取类名为 dropdown-toggle 的按钮元素并赋值给 dropdownToggle 变量用于触发下拉菜单的显示和隐藏
    var dropdownToggle = document.querySelector('.dropdown-toggle');
    // 获取类名为custom-dropdown-menu的下拉菜单元素并赋值给 dropdownMenu 变量
    var dropdownMenu = document.querySelector('.custom-dropdown-menu');
    // 为按钮添加一个 click 事件监听器，每次点击按钮时执行传入的回调函数。
    dropdownToggle.addEventListener('click', function() {
        // 切换下拉菜单的显示状态
        dropdownMenu.classList.toggle('show');
    });
    // 为整个文档添加一个click事件监听器，每次点击文档的任何地方都会执行传入的回调函数
    document.addEventListener('click', function(event) {
        // 判断点击的目标是否是按钮或下拉菜单内部的元素。如果点击的目标既不在按钮内，也不在下拉菜单内，则执行括号内的代码。
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});
*/

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