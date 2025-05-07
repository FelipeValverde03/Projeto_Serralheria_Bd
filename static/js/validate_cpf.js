function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');

    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;
    for (let i = 0; i < 9; i++)
        soma += parseInt(cpf.charAt(i)) * (10 - i);
    let resto = 11 - (soma % 11);
    if (resto >= 10) resto = 0;
    if (resto !== parseInt(cpf.charAt(9))) return false;

    soma = 0;
    for (let i = 0; i < 10; i++)
        soma += parseInt(cpf.charAt(i)) * (11 - i);
    resto = 11 - (soma % 11);
    if (resto >= 10) resto = 0;

    return resto === parseInt(cpf.charAt(10));
}

document.addEventListener("DOMContentLoaded", function () {
    const cpfInput = document.getElementById("cpf");
    const status = document.getElementById("cpf-status");

    if (!cpfInput || !status) return;

    cpfInput.addEventListener("input", function () {
        const cpf = cpfInput.value;

        if (cpf.length === 11) {
            if (validarCPF(cpf)) {
                status.textContent = "✅ CPF válido";
                status.style.color = "green";
            } else {
                status.textContent = "❌ CPF inválido";
                status.style.color = "red";
            }
        } else {
            status.textContent = "";
        }
    });
});
