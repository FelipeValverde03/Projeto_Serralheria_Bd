document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mudar-status-btn').forEach(button => {
    button.addEventListener('click', () => {
      const options = button.nextElementSibling;
      options.style.display = options.style.display === 'none' ? 'block' : 'none';
    });
  });

  document.querySelectorAll('.confirmar-status').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const container = btn.closest('.orcamento');
      const id = container.dataset.id;
      const select = container.querySelector('.novo-status');
      const status = select.value;

      if (status === "Cancelar" || !status) {
        container.querySelector('.status-options').style.display = 'none';
        return;
      }

      const res = await fetch('/mudar_status_ajax', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_orcamento: id, novo_status: status })
      });

      const data = await res.json();
      if (data.success) {
        window.location.reload();
      } else {
        alert("Erro ao mudar o status do orçamento.");
      }
    });
  });
});
