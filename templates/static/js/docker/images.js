function handlePullImage() {

    const name = document.getElementById('image-name-input').value

    if ( name === '' ) {
        alert('Please input image name');
        document.getElementById('image-name-input').focus();
        return
    }

    const tag =  document.getElementById('image-tag-input').value !== ''
        ? document.getElementById('image-tag-input').value
        : 'latest'

    console.log(`name = ${name}`);
    console.log(`tag = ${tag}`);

    fetch(`http://localhost:8000/api/dockers/images`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name,
            tag
        })
    })
        .then((resp) => resp.json())
        .then((data)=> {
            console.log(data);
            alert('test!');
        })
        .catch(
            (err) => {
                console.log(err);
            }
        );
}

