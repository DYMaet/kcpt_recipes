import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { recipesApi } from '../api';

const styles = {
  toast: {
    position: 'fixed',
    bottom: 24,
    right: 24,
    minWidth: 280,
    maxWidth: 380,
    padding: '14px 40px 14px 16px',
    background: '#1f2937',
    color: '#fff',
    borderRadius: 10,
    boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
    cursor: 'pointer',
    zIndex: 1000,
    animation: 'wsToastIn 0.25s ease-out',
    fontFamily: 'inherit',
    textAlign: 'left',
  },
  close: {
    position: 'absolute',
    top: 6,
    right: 8,
    background: 'transparent',
    border: 'none',
    color: '#9ca3af',
    fontSize: 20,
    lineHeight: 1,
    cursor: 'pointer',
  },
  header: { fontSize: 12, fontWeight: 600, color: '#a7f3d0', marginBottom: 4 },
  title:  { fontSize: 15, fontWeight: 600, marginBottom: 4 },
  meta:   { fontSize: 12, color: '#d1d5db' },
};

export default function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at_desc');
  const [search, setSearch] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [notification, setNotification] = useState(null);
  const notifTimerRef = useRef(null);
  const navigate = useNavigate();

  const fetch = async () => {
    setLoading(true);
    try {
      const { data } = await recipesApi.list({ page, per_page: 10, sort, search });
      setRecipes(data.recipes);
      setTotalPages(data.total_pages);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetch(); }, [page, sort, search]);

  // ---------- WebSocket: realtime "new recipe" notifications ----------
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    let closed = false;
    let reconnectTimer = null;
    let ws = null;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/ws/recipes?token=${encodeURIComponent(token)}`;

    const showNotification = (recipe) => {
      // Сбрасываем таймер прошлого уведомления (оно сейчас будет заменено)
      if (notifTimerRef.current) clearTimeout(notifTimerRef.current);
      // _ts как key — гарантирует перемонтирование тоста → анимация перезапускается
      setNotification({ ...recipe, _ts: Date.now() });
      notifTimerRef.current = setTimeout(() => setNotification(null), 6000);
    };

    const connect = () => {
      ws = new WebSocket(url);

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'new_recipe' && msg.recipe) {
            showNotification(msg.recipe);
          }
        } catch { /* ignore bad payloads */ }
      };

      ws.onclose = () => {
        if (!closed) reconnectTimer = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        try { ws.close(); } catch { /* noop */ }
      };
    };

    connect();

    return () => {
      closed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (notifTimerRef.current) clearTimeout(notifTimerRef.current);
      if (ws) { try { ws.close(); } catch { /* noop */ } }
    };
  }, []);
  // --------------------------------------------------------------------

  return (
    <div className="recipe-list-page">
      <style>{`
        @keyframes wsToastIn {
          from { transform: translateY(24px); opacity: 0; }
          to   { transform: translateY(0);    opacity: 1; }
        }
      `}</style>

      <div className="filters">
        <input
          type="text"
          placeholder="Поиск..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select value={sort} onChange={e => setSort(e.target.value)}>
          <option value="created_at_desc">Новые сначала</option>
          <option value="created_at_asc">Старые сначала</option>
          <option value="cook_time_asc">Время: по возрастанию</option>
          <option value="cook_time_desc">Время: по убыванию</option>
          <option value="calories_asc">Калории: по возрастанию</option>
          <option value="calories_desc">Калории: по убыванию</option>
        </select>
      </div>

      {loading ? <p>Загрузка...</p> : (
        <div className="recipes-grid">
          {recipes.map(r => (
            <Link to={`/recipe/${r.id}`} key={r.id} className="recipe-card">
              {r.image_url && <img src={r.image_url} alt={r.title} />}
              <h3>{r.title}</h3>
              <p>{r.description.slice(0, 100)}...</p>
              <div className="recipe-meta">
                <span>🔥 {r.calories} ккал</span>
                <span>⏱ {r.cook_time} мин</span>
                <span>👤 {r.author_name}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="pagination">
        <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>←</button>
        <span>Страница {page} из {totalPages}</span>
        <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>→</button>
      </div>

      {notification && (
        <div
          key={notification._ts}
          style={styles.toast}
          onClick={() => {
            setNotification(null);
            navigate(`/recipe/${notification.id}`);
          }}
          title="Открыть рецепт"
        >
          <button
            style={styles.close}
            onClick={(e) => { e.stopPropagation(); setNotification(null); }}
            aria-label="Закрыть"
          >×</button>
          <div style={styles.header}>🍳 Новый рецепт</div>
          <div style={styles.title}>{notification.title}</div>
          <div style={styles.meta}>
            👤 {notification.author_name} · 🔥 {notification.calories} ккал · ⏱ {notification.cook_time} мин
          </div>
        </div>
      )}
    </div>
  );
}