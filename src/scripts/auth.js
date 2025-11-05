document.addEventListener('DOMContentLoaded', function() {

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const authUrl = window.API_CONFIG?.auth || 'http://localhost:8001';
                const response = await fetch(`${authUrl}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                if (response.status === 201) {
                    alert('Регистрация прошла успешно! Теперь вы можете войти.');
                    window.location.href = 'login.html';
                } else {
                    const data = await response.json();
                    alert('Ошибка регистрации: ' + (data.detail || 'Неизвестная ошибка'));
                }
            } catch (error) {
                alert('Произошла ошибка сети. Попробуйте снова.');
            }
        });
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            try {
                const authUrl = window.API_CONFIG?.auth || 'http://localhost:8001';
                const response = await fetch(`${authUrl}/token`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('accessToken', data.access_token);
                    alert('Вход выполнен успешно!');
                    window.location.href = 'index.html';
                } else {
                    const data = await response.json();
                    alert('Ошибка входа: ' + (data.detail || 'Неправильный email или пароль'));
                }
            } catch (error) {
                alert('Произошла ошибка сети. Попробуйте снова.');
            }
        });
    }

});
