import { validarCPF } from './validate_cpf.js';
import { validarCNPJ } from './validate_cnpj.js';

document.addEventListener("DOMContentLoaded", function () {
    const tipoDocRadios = document.getElementsByName("tipo_doc");
    const docInput = document.getElementById("documento");
    const docStatus = document.getElementById("doc-status");
    const docLabel = document.getElementById("doc-label");

    function atualizarValidacao() {
        const tipoSelecionado = document.querySelector('input[name="tipo_doc"]:checked').value;
        const valor = docInput.value;

        if (tipoSelecionado === "cpf") {
            docLabel.textContent = "CPF:";
            docInput.maxLength = 11;

            if (valor.length === 11) {
                const valido = validarCPF(valor);
                docStatus.textContent = valido ? "✅ CPF válido" : "❌ CPF inválido";
                docStatus.style.color = valido ? "green" : "red";
            } else {
                docStatus.textContent = "";
            }
        } else if (tipoSelecionado === "cnpj") {
            docLabel.textContent = "CNPJ:";
            docInput.maxLength = 14;

            if (valor.length === 14) {
                const valido = validarCNPJ(valor);
                docStatus.textContent = valido ? "✅ CNPJ válido" : "❌ CNPJ inválido";
                docStatus.style.color = valido ? "green" : "red";
            } else {
                docStatus.textContent = "";
            }
        }
    }

    // Quando digita no campo
    docInput.addEventListener("input", atualizarValidacao);

    // Quando troca CPF/CNPJ
    tipoDocRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            docInput.value = "";
            docStatus.textContent = "";
            atualizarValidacao();
        });
    });
});
