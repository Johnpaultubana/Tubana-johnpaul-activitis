//checkNumber
function checkNumber() {
    const guess = document.getElementById('guess ').value;

    if(guess == random) {
        document.getElementById('message').innerHTML = "correct";
    }
    else {
        document.getElementById('message').innerHTML = "wrong";
    }
}