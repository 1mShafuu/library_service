INSERT INTO addresses (city_name, street_name) VALUES
('Springfield', 'Maple St'),
('Metropolis', 'Oak St'),
('Gotham', 'Pine St'),
('Star City', 'Birch St'),
('Central City', 'Elm St'),
('Smalltown', 'Cedar St'),
('Hometown', 'Elm St');

INSERT INTO readers (name, address_id, last_visit) VALUES
('John Doe', 1, '2024-09-20'),
('Jane Smith', 2, '2024-09-18'),
('Emily Johnson', 3, '2024-09-15'),
('Michael Brown', 4, '2024-09-19'),
('Sarah Davis', 5, '2024-09-17'),
('Anna Green', 6, '2024-09-10'),
('Tom White', 7, '2024-09-22');

INSERT INTO authors (name) VALUES
('George Orwell'), ('J.K. Rowling'), ('Leo Tolstoy'), 
('Mark Twain'), ('Jane Austen'), ('F. Scott Fitzgerald'), 
('Isaac Asimov'), ('Agatha Christie'), ('Stephen King'), 
('Arthur Conan Doyle');

INSERT INTO books (title, genre, author_id) VALUES
('1984', 'Dystopian', 1),
('Harry Potter and the Sorcerer\'s Stone', 'Fantasy', 2),
('War and Peace', 'Historical Fiction', 3),
('The Adventures of Tom Sawyer', 'Adventure', 4),
('Pride and Prejudice', 'Romance', 5),
('The Great Gatsby', 'Classic', 6),
('Foundation', 'Science Fiction', 7),
('Murder on the Orient Express', 'Mystery', 8),
('The Shining', 'Horror', 9),
('The Hound of the Baskervilles', 'Mystery', 10);

INSERT INTO book_loans (book_id, reader_id, loan_date, return_date, expected_return_date) VALUES
(1, 1, '2024-09-01', NULL, '2024-09-15'),
(2, 2, '2024-09-03', '2024-09-10', '2024-09-17'),
(3, 3, '2024-09-05', NULL, '2024-09-19'),
(4, 4, '2024-09-07', NULL, '2024-09-21'),
(5, 5, '2024-09-09', '2024-09-20', '2024-09-23'),
(6, 6, '2024-09-15', NULL, '2024-09-29'),
(7, 7, '2024-09-17', NULL, '2024-09-30'),
(8, 1, '2024-09-20', '2024-09-24', '2024-09-26'),
(9, 2, '2024-09-21', NULL, '2024-09-25'),
(10, 3, '2024-09-22', NULL, '2024-09-28');
