const rutScreen = document.querySelector('#rut-screen');
const codeScreen = document.querySelector('#code-screen');
const invoicesScreen = document.querySelector('#invoices-screen');
const rutForm = document.querySelector('#rut-form');
const codeForm = document.querySelector('#code-form');
const rutInput = document.querySelector('#rut');
const codeInputs = [...document.querySelectorAll('#code-inputs input')];
const rutError = document.querySelector('#rut-error');
const codeError = document.querySelector('#code-error');
const companyEmail = document.querySelector('#company-email');
const invoiceList = document.querySelector('#invoice-list');
const invoiceMessage = document.querySelector('#invoice-message');
let currentRut = '';
let failedAttempts = 0;
let sessionToken = '';

function cleanRut(value) {
  return value.toUpperCase().replace(/[^0-9K]/g, '');
}

function formatRut(value) {
  const cleanValue = cleanRut(value).slice(0, 9);
  if (cleanValue.length < 2) return cleanValue;
  const body = cleanValue.slice(0, -1).replace(/\D/g, '');
  const checkDigit = cleanValue.slice(-1);
  const formattedBody = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${formattedBody}-${checkDigit}`;
}

function isValidRut(value) {
  try {
    return Boolean(window.Rut && new window.Rut(cleanRut(value)).isValid);
  } catch {
    return false;
  }
}

function showScreen(screen) {
  [rutScreen, codeScreen, invoicesScreen].forEach((item) => {
    const visible = item === screen;
    item.hidden = !visible;
    item.classList.toggle('active', visible);
  });
}

rutInput.addEventListener('input', () => {
  rutInput.value = formatRut(rutInput.value);
  rutError.textContent = '';
});

rutForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  rutError.textContent = '';
  if (!isValidRut(rutInput.value)) {
    rutError.textContent = 'Ingresa un RUT válido.';
    rutInput.focus();
    return;
  }
  const response = await fetch('/api/access', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rut: rutInput.value }),
  });
  const data = await response.json();
  if (!response.ok) {
    rutError.textContent = data.error;
    return;
  }
  currentRut = data.rut;
  failedAttempts = 0;
  companyEmail.textContent = data.email;
  codeInputs.forEach((input) => { input.value = ''; input.disabled = false; });
  codeForm.querySelector('button').disabled = false;
  showScreen(codeScreen);
  codeInputs[0].focus();
});

codeInputs.forEach((input, index) => {
  input.addEventListener('input', () => {
    input.value = input.value.replace(/\D/g, '').slice(0, 1);
    if (input.value && codeInputs[index + 1]) codeInputs[index + 1].focus();
  });
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Backspace' && !input.value && codeInputs[index - 1]) codeInputs[index - 1].focus();
  });
});

codeForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  codeError.textContent = '';
  const code = codeInputs.map((input) => input.value).join('');
  const response = await fetch('/api/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rut: currentRut, code }),
  });
  const data = await response.json();
  if (!response.ok) {
    failedAttempts += 1;
    codeError.textContent = failedAttempts >= 3
      ? 'Has superado el número de intentos. Solicita un nuevo código.'
      : 'El código ingresado no es correcto.';
    if (failedAttempts >= 3) {
      codeInputs.forEach((input) => { input.disabled = true; });
      codeForm.querySelector('button').disabled = true;
    }
    return;
  }
  sessionToken = data.token;
  await loadInvoices();
});

document.querySelector('#back-button').addEventListener('click', () => {
  showScreen(rutScreen);
  rutInput.focus();
});

async function loadInvoices() {
  const response = await fetch('/api/invoices', {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const data = await response.json();
  invoiceList.innerHTML = data.invoices.map((invoice) => `
    <button class="invoice-row" data-invoice-id="${invoice.id}" type="button">
      <span><strong>${invoice.number}</strong><small>${invoice.date}</small></span>
      <span class="amount">${invoice.amount}<b>›</b></span>
    </button>
  `).join('');
  invoiceList.querySelectorAll('.invoice-row').forEach((row) => {
    row.addEventListener('click', () => openInvoice(row.dataset.invoiceId));
  });
  showScreen(invoicesScreen);
}

async function openInvoice(invoiceId) {
  invoiceMessage.textContent = 'Cargando detalle...';
  const response = await fetch(`/api/invoices/${invoiceId}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const data = await response.json();
  invoiceMessage.textContent = data.message;
}
