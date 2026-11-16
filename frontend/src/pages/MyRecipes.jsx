import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { myRecipesApi } from '../api';

export default function MyRecipes() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const navigate = useNavigate();

  const fetch = async () => {
    setLoading(true);
    try {
      const { data } = await myRecipesApi.list({ page, per_page: 10 });
      setRecipes(data.recipes);
      setTotalPages(data.total_pages);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetch(); }, [page]);

  const handleDelete = async (id) => {
    if (!confirm('Удалить рецепт?')) return;
    await myRecipesApi.delete(id);
    fetch();
  };

  return (
    <div className="my-recipes-page">
      <div className="page-header">
        <h1>Мои рецепты</h1>
        <Link to="/create-recipe" className="btn btn-primary">Создать рецепт</Link>
      </div>

      {loading ? <p>Загрузка...</p> : (
        <div className="recipes-grid">
          {recipes.map(r => (
            <div key={r.id} className="recipe-card my-recipe-card">
              {r.image_url && <img src={r.image_url} alt={r.title} />}
              <h3>{r.title}</h3>
              <p>{r.description.slice(0, 100)}...</p>
              <div className="recipe-meta">
                <span>🔥 {r.calories} ккал</span>
                <span>⏱ {r.cook_time} мин</span>
              </div>
              <div className="recipe-actions">
                <Link to={`/edit-recipe/${r.id}`} className="btn">Редактировать</Link>
                <button className="btn btn-danger" onClick={() => handleDelete(r.id)}>Удалить</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="pagination">
        <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>←</button>
        <span>Страница {page} из {totalPages}</span>
        <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>→</button>
      </div>
    </div>
  );
}