-- AradLens - categorii de test (idempotent)
-- Ruleaza dupa ce tabela categories exista (sql/006...).
-- INSERT IGNORE: nu face nimic daca numele exista deja.

INSERT IGNORE INTO categories (name) VALUES
    ('Parcuri'),
    ('Clădiri istorice'),
    ('Muzee'),
    ('Biserici'),
    ('Monumente'),
    ('Piețe'),
    ('Poduri'),
    ('Statui'),
    ('Turnuri'),
    ('Galerii de artă'),
    ('Cafenele'),
    ('Restaurante');
