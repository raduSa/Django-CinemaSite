var ticket_data;

// get data about current cart
function load_cart() {
    fetch('http://localhost:8000/app1/get_difuzare_data')
    .then(response => response.json())
    .then(data => {
        tickets = data['tickets'];
        const cart = JSON.parse(localStorage.getItem("cart")) || {};
        const tableBody = document.querySelector('#cartTable tbody');
        tableBody.innerHTML = '';
        let totalItems = 0;
        let totalPrice = 0;
        console.log(tickets);

        tickets = tickets.filter(ticket => {
            if (ticket.id in cart) {
                const ticket_price = parseFloat(ticket.pret_bilet).toFixed(2);
                const subtotal = ticket_price * cart[ticket.id];

                // save how many tickets have been bought inside the json
                ticket.nr_bilete = cart[ticket.id];

                totalItems += cart[ticket.id];
                totalPrice += subtotal;

                const row = `
                <tr>
                    <td>${ticket.film__titlu}</td>
                    <td class="text-right">${ticket_price}</td>
                    <td class="text-right">${ticket.timp_start}</td>
                    <td class="text-right">${ticket.sala__numar}</td>
                    <td class="text-right">${cart[ticket.id]}</td>
                    <td class="text-right">${subtotal}</td>
                </tr>`;
                tableBody.innerHTML += row;
                return true;
            }
            else {
                return false;
            }
        });

        ticket_data = tickets;

        // update totals
        document.getElementById('totalItems').textContent = totalItems;
        document.getElementById('totalPrice').textContent = totalPrice.toFixed(2);

        promos = data['promos'];
        console.log(promos);
        promos.forEach(promo => {
            const row = `
            <li>
                <span class="promo-category">Categoria: ${promo.category}</span> - 
                <span class="promo-discount">${promo.discount}%</span>
                <span class="promo-name">${promo.name}</span>
                <a class="promo-link" href="/app1/promotie/${promo.id}">Pagina promotie</a>
            </li>
            `;
            document.getElementById('promo-list').innerHTML += row;
        })
    })
    .catch(error => console.error('Error:', error));
}
    
// sort table fucntion
function sortTable(columnIndex, numeric = false) {
    const table = document.getElementById('cartTable');
    const rows = Array.from(table.rows).slice(1);
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].innerText;
        const bText = b.cells[columnIndex].innerText;

        if (numeric) {
            return parseFloat(aText) - parseFloat(bText);
        }
        return aText.localeCompare(bText);
    });

    rows.forEach(row => table.tBodies[0].appendChild(row)); // Reorder rows in table
}
        
window.onload = function() {
    load_cart();

    // set up buy button
    var btn_cumpara=document.getElementById("buy");
    btn_cumpara.onclick = function() {
        // delete cart from localStorage
        localStorage.setItem("cart", JSON.stringify({}));

        fetch('http://localhost:8000/app1/proceseaza_date', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken ,
            },
            body: JSON.stringify(ticket_data)
        })
            .then(raspuns => {
                if (!raspuns.ok) {
                    throw new Error(`Eroare HTTP. Status: ${raspuns.status}`);
                }
                return raspuns.text();
            })
            .then(date => {
                console.log('Raspuns:', date);
            })
            .catch(eroare => {
                console.error('Eroare:', eroare);
            });
        load_cart();
    }
    
    // set up empty button
    var btn_empty = document.getElementById("empty");
    btn_empty.onclick = function() {
        // delete cart from localStorage
        localStorage.setItem("cart", JSON.stringify({}));
        load_cart();
    }
}