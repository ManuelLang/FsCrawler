-- Number of files by extension
select extension, count(*)
from path
where extension <> ''
group by extension
order by count(*) DESC, extension;

-- Sum of files' size by extension
select extension, sum(size_in_mb)
from path
where extension <> ''
group by extension
order by sum(size_in_mb) DESC, extension;

-- Find duplicates
Select p.size_in_mb, p.hash, p.`path`
FROM `path` p
Inner Join `path` p1 on p.size_in_mb = p1.size_in_mb AND p.hash = p1.hash AND p.`path` <> p1.`path`
Where p.hash <> '' AND p.hash  IS NOT NULL
Order By p.size_in_mb DESC, p.hash, p.`path`;

-- Same but using sub-query: inaccurate because no filter on filesize; hence we might have collisions
Select p1.hash, p1.size_in_mb, p1.path
From `path` p1
WHERE p1.hash IN (
	select p.hash
	from `path` p
	where p.hash <> ''
	group by p.hash
	having count(1) > 1
	order by count(1) DESC
)
order by p1.hash, p1.size_in_mb DESC, p1.path;