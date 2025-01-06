window.onload = function(){
    // get current cart from local storage
    const cart = JSON.parse(localStorage.getItem("cart")) || {};

    // update on page reload
    for (let id in cart) {
        let quantity_input = document.getElementById("input_difuzare-" + id);
        if (quantity_input) {
            quantity_input.setAttribute("value", cart[id]);
            quantity_input.value = cart[id];
        }
        let article = document.getElementById("difuzare-" + id);
        if (article) {
            article.classList.add("added_to_cart");
        }
    }

    updateCart = function(id, count, max_count) {
        if (count > max_count) {
            alert("Sunt valabile doar " + max_count + " bilete");
            return;
        }
        if (count > 0) {
            cart[id] = count;
        }
        else {
            delete cart[id];
        }
        localStorage.setItem("cart", JSON.stringify(cart));
        let quantity_input = document.getElementById("input_difuzare-" + id);
        if (quantity_input) {
            quantity_input.value = count;
        }
    }
    // add to cart buttons
    var buttons = document.getElementsByClassName("add_to_cart");
    for(let btn of buttons){
        btn.onclick = function(){
            let id = btn.dataset.id;
            let max_count = btn.dataset.count;
            let count = 0;
            if (id in cart) {
                count = cart[id];
            }
            updateCart(id, count + 1, max_count);
            article = document.getElementById("difuzare-" + id);
            console.log(article);
            article.classList.add("added_to_cart");
        }
    }
    // delete from cart buttons
    var buttons = document.getElementsByClassName("remove_from_cart");
    for (let btn of buttons) {
        btn.onclick = function () {
            let id = btn.dataset.id;
            let count = 0;
            updateCart(id, count, 0);
            article = document.getElementById("difuzare-" + id);
            article.classList.remove("added_to_cart");
        }
    }
    // increase buttons
    var buttons = document.getElementsByClassName("increase");
    for (let btn of buttons) {
        btn.onclick = function () {
            let id = btn.dataset.id;
            let count = cart[id];
            let max_count = parseInt(btn.dataset.count);
            updateCart(id, count + 1, max_count);
        }
    }
    // decrease buttons
    var buttons = document.getElementsByClassName("decrease");
    for (let btn of buttons) {
        btn.onclick = function () {
            let id = btn.dataset.id;
            let count = cart[id];
            let max_count = parseInt(btn.dataset.count);
            if (count == 1) {
                article = document.getElementById("difuzare-" + id);
                article.classList.remove("added_to_cart");
                updateCart(id, 0, max_count);
            }
            else {
                updateCart(id, count - 1, max_count);
            }
        }
    }
    // quantity inputs
    var inputs = document.getElementsByClassName("quantity");
    for (let input of inputs) {
        input.onchange = function () {
            let id = input.dataset.id;
            let count = parseInt(input.value);
            let max_count = parseInt(input.getAttribute("max"));
            updateCart(id, count, max_count);
        }
    }
}