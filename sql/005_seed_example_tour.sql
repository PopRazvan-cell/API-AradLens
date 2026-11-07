-- AradLens - tur demonstrativ bazat pe locatiile existente
-- Ruleaza dupa ce tabelele tours / tour_locations exista (sql/004...).
-- Este idempotent: creeaza turul doar daca nu exista deja niciun tur.

SET @has_tours := (SELECT COUNT(*) FROM tours);

INSERT INTO tours (name, description)
SELECT 'Turul Centrului', 'Traseu demonstrativ prin punctele de interes existente.'
WHERE @has_tours = 0;

SET @created := ROW_COUNT();
SET @tour_id := LAST_INSERT_ID();
SET @pos := 0;

INSERT INTO tour_locations (tour_id, location_id, `position`)
SELECT @tour_id, l.id, (@pos := @pos + 1)
FROM locations l
WHERE @created = 1
ORDER BY l.id;
