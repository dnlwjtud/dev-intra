function handlePullImage() {

    const name = document.getElementById('image-name-input');

    if ( name.value === '' ) {
        alert('Please input image name');
        document.getElementById('image-name-input').focus();
        return;
    }

    const tag =  document.getElementById('image-tag-input');

    name.disabled = true;
    tag.disabled = true;

    const btnCon = document.getElementById('modal-btn-con');

    const clsBtn = document.getElementById('image-pull-close-btn');
    const execBtn = document.getElementById('image-pull-exec-btn');
    const loadingCircle = createLoadingCircleBtn();

    loadingCircle.disabled = true;

    execBtn.remove();
    btnCon.prepend(loadingCircle);

    fetch(`http://localhost:8000/api/dockers/images`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name.value,
            tag: tag.value !== ''
                ? tag.value
                : 'latest'
        })
    })
        .then((resp) => resp.json())
        .then((data)=> {

            const con = document.getElementById('toast-con-btn');
            const toast = data.status === 200
                ? createToast(data.msg, 'success')
                : createToast(data.msg, 'danger');

            con.appendChild(toast);
            const obj = new bootstrap.Toast(toast);

            obj.show();

        })
        .catch(
            (err) => console.log(err)
        ).finally(
        () => {

            name.value = '';
            tag.value = '';

            name.disabled = false;
            tag.disabled = false;

            loadingCircle.remove();
            btnCon.prepend(execBtn);

            clsBtn.click();

        }
    );

}

