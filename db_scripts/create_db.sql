CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(50),
    street_name VARCHAR(50)
);

CREATE TABLE readers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address_id INT REFERENCES addresses(id) ON DELETE CASCADE,
    last_visit DATE
);

CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    CONSTRAINT unique_author_name UNIQUE (name)
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    author_id INT REFERENCES authors(id)
);

CREATE TABLE book_loans (
    id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(id),
    reader_id INT REFERENCES readers(id),
    loan_date DATE NOT NULL,
    return_date DATE,
    expected_return_date DATE
);
