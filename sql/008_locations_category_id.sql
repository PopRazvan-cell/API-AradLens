-- AradLens - o singura categorie per locatie
-- Inlocuieste vechea tabela many-to-many location_categories cu locations.category_id.
-- Ruleaza dupa sql/006_create_categories_tables.sql.
-- ATENTIE: DROP TABLE location_categories este distructiv (se pierd asignarile vechi).

ALTER TABLE locations
    ADD COLUMN category_id BIGINT UNSIGNED NULL,
    ADD KEY idx_locations_category_id (category_id),
    ADD CONSTRAINT fk_locations_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
        ON DELETE SET NULL;

DROP TABLE IF EXISTS location_categories;
