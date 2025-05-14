
document.addEventListener("DOMContentLoaded", function () {
    const botoes = document.querySelectorAll(".entrega-btn");

    botoes.forEach(btn => {
        btn.addEventListener("click", function () {
            const idObra = this.getAttribute("data-id");

            fetch("/entregar_obra", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ id_obra: idObra })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert("Erro: " + data.message);
                }
            })
            .catch(err => {
                alert("Erro na requisição: " + err);
            });
        });
    });
});
