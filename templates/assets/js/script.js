document.addEventListener("DOMContentLoaded", function () {
    // Handle login (dummy authentication)
    const loginForm = document.querySelector("form");
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault();
            localStorage.setItem("user", "testuser");
            window.location.href = "dashboard.html";
        });
    }

    // Handle logout
    const logoutBtn = document.querySelector(".btn-light");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            localStorage.removeItem("user");
            window.location.href = "index.html";
        });
    }

    // Show user data on Dashboard
    const user = localStorage.getItem("user");
    if (user && document.querySelector(".dashboard-container")) {
        document.querySelector("strong").innerText = user;
    }

    // Update balance
    let balance = parseFloat(localStorage.getItem("balance")) || 0;
    document.querySelectorAll(".balance").forEach(el => el.innerText = `Balance: $${balance.toFixed(2)}`);

    // Send money function
    const sendMoneyForm = document.querySelector("#sendMoneyForm");
    if (sendMoneyForm) {
        sendMoneyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            let amount = parseFloat(document.querySelector("#amount").value);
            if (amount > 0 && amount <= balance) {
                balance -= amount;
                localStorage.setItem("balance", balance);
                alert(`You sent $${amount}`);
                window.location.href = "dashboard.html";
            } else {
                alert("Insufficient balance!");
            }
        });
    }
});
