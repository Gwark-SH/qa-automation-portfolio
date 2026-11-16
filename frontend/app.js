const API_BASE_URL = "http://localhost:8000";

// 토스트 메시지 노출 (2.5초 후 자동 숨김)
function showToast(message) {
    const toast = document.getElementById('toast-msg');
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 2500);
}

// 로그인 상태에 따라 폼 활성화/비활성화 동기화
function syncAuthUI() {
    const token = localStorage.getItem('qa_token');
    const username = localStorage.getItem('qa_user');
    const isLogged = Boolean(token);

    document.getElementById('login-form').classList.toggle('hidden', isLogged);
    document.getElementById('user-info').classList.toggle('hidden', !isLogged);
    document.getElementById('auth-notice').classList.toggle('hidden', isLogged);

    if (isLogged) {
        document.getElementById('welcome-msg').textContent = `${username}님 환영합니다`;
    }

    ['new-name', 'new-category', 'new-rating', 'new-tag', 'add-btn'].forEach(id => {
        document.getElementById(id).disabled = !isLogged;
    });
}

async function handleLogin() {
    const username = document.getElementById('username-input').value;
    const password = document.getElementById('password-input').value;

    const res = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('qa_token', data.access_token);
        localStorage.setItem('qa_user', data.username);
        syncAuthUI();
        await fetchRestaurants();
        showToast("로그인되었습니다.");
    } else {
        showToast("로그인 실패: 계정 정보를 확인하세요.");
    }
}

function handleLogout() {
    localStorage.removeItem('qa_token');
    localStorage.removeItem('qa_user');
    syncAuthUI();
    fetchRestaurants();
    showToast("로그아웃되었습니다.");
}

async function fetchRestaurants() {
    const category = document.getElementById('category-select').value;
    const keyword = document.getElementById('search-input').value;
    const listEl = document.getElementById('restaurant-list');
    const emptyEl = document.getElementById('empty-msg');
    const errorEl = document.getElementById('error-msg');
    const loadingEl = document.getElementById('loading-spinner');
    const isLogged = Boolean(localStorage.getItem('qa_token'));

    listEl.innerHTML = '';
    emptyEl.classList.add('hidden');
    errorEl.classList.add('hidden');
    loadingEl.classList.remove('hidden');

    try {
        const params = new URLSearchParams({ category, keyword });
        const res = await fetch(`${API_BASE_URL}/api/restaurants?${params.toString()}`);
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);

        const data = await res.json();
        loadingEl.classList.add('hidden');

        if (data.length === 0) {
            emptyEl.classList.remove('hidden');
            return;
        }

        data.forEach(item => {
            const card = document.createElement('div');
            card.setAttribute('data-testid', 'restaurant-card');
            card.className = 'bg-white p-5 rounded-lg shadow hover:shadow-md transition relative';
            
            const deleteBtnHtml = isLogged 
                ? `<button data-testid="delete-btn" onclick="deleteRestaurant(${item.id}, '${item.name}')" class="text-xs text-red-500 hover:underline mt-3 block">삭제</button>` 
                : '';

            card.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <h2 data-testid="card-name" class="text-xl font-bold">${item.name}</h2>
                    <span data-testid="card-rating" class="bg-yellow-100 text-yellow-800 text-sm font-semibold px-2.5 py-0.5 rounded">★ ${item.rating}</span>
                </div>
                <p data-testid="card-category" class="text-sm text-gray-500 mb-3">${item.category}</p>
                <span data-testid="card-tag" class="inline-block bg-blue-50 text-blue-600 text-xs px-2 py-1 rounded font-medium">#${item.ai_tag}</span>
                ${deleteBtnHtml}
            `;
            listEl.appendChild(card);
        });
    } catch (err) {
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
    }
}

async function addRestaurant() {
    const name = document.getElementById('new-name').value;
    const category = document.getElementById('new-category').value;
    const rating = parseFloat(document.getElementById('new-rating').value);
    const ai_tag = document.getElementById('new-tag').value;
    const token = localStorage.getItem('qa_token');

    const res = await fetch(`${API_BASE_URL}/api/restaurants`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ name, category, rating, ai_tag })
    });

    if (res.ok) {
        document.getElementById('new-name').value = '';
        document.getElementById('new-rating').value = '';
        document.getElementById('new-tag').value = '';
        showToast("새 맛집이 등록되었습니다!");
        await fetchRestaurants();
    } else {
        document.getElementById('error-msg').classList.remove('hidden');
    }
}

async function deleteRestaurant(id, name) {
    // 브라우저 기본 Confirm 대화상자 호출 (Playwright dialog 제어 연습용)
    if (!window.confirm(`정말 '${name}' 맛집을 삭제하시겠습니까?`)) return;

    const token = localStorage.getItem('qa_token');
    const res = await fetch(`${API_BASE_URL}/api/restaurants/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
        showToast("삭제되었습니다.");
        await fetchRestaurants();
    }
}

document.getElementById('login-btn').addEventListener('click', handleLogin);
document.getElementById('logout-btn').addEventListener('click', handleLogout);
document.getElementById('search-btn').addEventListener('click', fetchRestaurants);
document.getElementById('add-btn').addEventListener('click', addRestaurant);

window.onload = () => {
    syncAuthUI();
    fetchRestaurants();
};