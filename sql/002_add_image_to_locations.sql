-- Adauga coloana pentru poza cladirii in tabela locations
ALTER TABLE locations
    ADD COLUMN image VARCHAR(500) NULL;
