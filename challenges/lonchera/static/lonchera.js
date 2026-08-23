const token = localStorage.getItem('lonchera_token');
const state = { items: {}, catalog: [], credits: 0 };

const money = value => `${Number(value).toLocaleString('es-CL')} créditos`;

async function api(path, options = {}) {
    const response = await fetch(path, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...(options.headers || {})
        }
    });
    return response.json();
}

function show(message, error = false) {
    const notice = document.getElementById('notice');
    notice.textContent = message;
    notice.className = `notice${error ? ' error' : ''}`;
}

function render() {
    document.getElementById('items').innerHTML = state.catalog.map(item => `
        <article class="item">
            <div class="emoji">${item.emoji}</div>
            <h2>${item.name}</h2>
            <p>${item.description}</p>
            <div class="item-footer">
                <span class="price">${money(item.price)}${item.stock === 1 ? '<small> · 1 disponible</small>' : ''}</span>
                <button data-add="${item.id}">Añadir</button>
            </div>
        </article>
    `).join('');

    document.querySelectorAll('[data-add]').forEach(button => {
        button.onclick = () => {
            const id = button.dataset.add;
            state.items[id] = Math.min((state.items[id] || 0) + 1, 100);
            renderCart();
        };
    });
    renderCart();
}

function renderCart() {
    const entries = Object.entries(state.items).filter(([, quantity]) => quantity > 0);
    document.getElementById('cart').innerHTML = entries.length ? entries.map(([id, quantity]) => {
        const item = state.catalog.find(candidate => candidate.id === id);
        return `
            <div class="cart-line">
                <div>${item.name}<small>${money(item.price)} c/u</small></div>
                <input type="number" max="100" value="${quantity}" data-quantity="${id}">
                <button class="remove" type="button" data-remove="${id}">Quitar</button>
            </div>
        `;
    }).join('') : '<p class="notice">Tu lonchera está vacía.</p>';

    document.querySelectorAll('[data-quantity]').forEach(input => {
        input.onchange = () => {
            const value = Number(input.value);
            if (!Number.isInteger(value) || value < 1 || value > 100) {
                input.value = state.items[input.dataset.quantity] || 1;
                show('Las cantidades deben estar entre 1 y 100.', true);
                return;
            }
            state.items[input.dataset.quantity] = value;
            renderCart();
        };
    });

    document.querySelectorAll('[data-remove]').forEach(button => {
        button.onclick = () => {
            delete state.items[button.dataset.remove];
            renderCart();
        };
    });

    const total = entries.reduce((sum, [id, quantity]) => {
        return sum + state.catalog.find(item => item.id === id).price * quantity;
    }, 0);
    document.getElementById('total').textContent = money(total);
}

async function load() {
    const data = await api('/api/items');
    if (data.error) {
        localStorage.removeItem('lonchera_token');
        location.href = '/';
        return;
    }
    state.catalog = data.items;
    state.credits = data.credits;
    document.getElementById('balance').textContent = Number(data.credits).toLocaleString('es-CL');
    render();
}

const logout = document.getElementById('logout');
if (logout) {
    logout.onclick = async () => {
        await api('/api/logout', { method: 'POST' });
        localStorage.removeItem('lonchera_token');
        location.href = '/';
    };
}

const checkout = document.getElementById('checkout');
if (checkout) {
    checkout.onclick = async () => {
        const quantities = Object.fromEntries(Object.entries(state.items).filter(([, quantity]) => quantity > 0));
        if (!Object.keys(quantities).length) return show('Añade algo a tu lonchera primero.', true);
        const invalid = Object.values(quantities).some(quantity => !Number.isInteger(quantity) || quantity < 1 || quantity > 100);
        if (invalid) return show('Las cantidades deben estar entre 1 y 100.', true);
        const total = Object.entries(quantities).reduce((sum, [id, quantity]) => {
            return sum + state.catalog.find(item => item.id === id).price * quantity;
        }, 0);
        if (total > state.credits) return show('No tienes suficientes créditos.', true);
        const body = { items: quantities };
        console.log('Checkout request body:', body);
        const data = await api('/api/checkout', { method: 'POST', body: JSON.stringify(body) });
        if (data.error) return show(data.error, true);
        state.credits = data.credits;
        document.getElementById('balance').textContent = Number(data.credits).toLocaleString('es-CL');
        state.items = {};
        renderCart();
        show(data.message);
    };
}

if (checkout) load();

const login = document.getElementById('login');
if (login) {
    login.onsubmit = async event => {
        event.preventDefault();
        const form = new FormData(event.target);
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Object.fromEntries(form))
        });
        const data = await response.json();
        if (!response.ok) {
            document.getElementById('error').textContent = data.error;
            return;
        }
        localStorage.setItem('lonchera_token', data.token);
        location.href = '/shop';
    };
}
