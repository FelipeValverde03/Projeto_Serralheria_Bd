document.addEventListener("DOMContentLoaded", function () {
    const selectPagamento = document.getElementById('forma_pagamento');
    const campoOutro = document.createElement('div');
    campoOutro.id = 'campo_outro_pagamento';
    selectPagamento.insertAdjacentElement('afterend', campoOutro);
  
    selectPagamento.addEventListener('change', function () {
      if (this.value === 'Outro') {
        campoOutro.innerHTML = `
          <br><br>
          <label for="outra_forma">Digite a forma de pagamento:</label>
          <input type="text" id="outra_forma" name="outra_forma" required />
        `;
      } else {
        campoOutro.innerHTML = '';
      }
    });
  });