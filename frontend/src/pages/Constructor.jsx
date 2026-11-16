import { useState, useEffect } from 'react';
import { recipesApi, ingredientsApi } from '../api';

export default function Constructor() {
  const [allIngredients, setAllIngredients] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    ingredientsApi.list().then(r => setAllIngredients(r.data.ingredients));
  }, []);

  const toggle = (id) => {
    setSelectedIds(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  };

  const search = async () => {
    if (!selectedIds.length) return;
    setLoading(true);
    try {
      const { data } = await recipesApi.searchByIngredients(selectedIds, { per_page: 20 });
      setResults(data.recipes);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <div className="constructor-page">
      <h1>Конструктор рецептов</h1>
      <div className="constructor-layout">
        <aside className="ingredients-panel">
          <h3>Ингредиенты</h3>
          <p>Нажмите на ингредиент чтобы добавить/убрать</p>
          <div className="ingredients-grid">
            {allIngredients.map(i => (
              <div key={i.id} className={`ingredient-tag ${selectedIds.includes(i.id) ? 'selected' : ''}`} onClick={() => toggle(i.id)}>
                {i.name}
              </div>
            ))}
          </div>
          <div className="selected-count">
            Выбрано: {selectedIds.length}
            <button onClick={search} disabled={!selectedIds.length || loading} className="btn btn-primary">
              {loading ? 'Поиск...' : 'Найти рецепты'}
            </button>
          </div>
        </aside>
        <section className="results-panel">
          <h3>Результаты</h3>
          {loading ? <p>Поиск...</p> : results.length ? (
            <div className="recipes-grid">
              {results.map(r => (
                <a href={`/recipe/${r.id}`} key={r.id} className="recipe-card">
                  {r.image_url && <img src={r.image_url} alt={r.title} />}
                  <h4>{r.title}</h4>
                  <p>{r.description.slice(0, 80)}...</p>
                  <div className="recipe-meta">
                    <span>🔥 {r.calories}</span>
                    <span>⏱ {r.cook_time} мин</span>
                  </div>
                </a>
              ))}
            </div>
          ) : selectedIds.length ? <p>Ничего не найдено</p> : <p>Выберите ингредиенты слева</p>}
        </section>
      </div>
    </div>
  );
}