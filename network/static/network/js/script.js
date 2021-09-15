document.addEventListener('DOMContentLoaded', function() {
	console.log('oi');
});

function edit(id) {
	let edit_box = document.querySelector(`#edit-box-${id}`);
	let edit_button = document.querySelector(`#edit-button-${id}`);

	if (edit_box.classList.contains("d-none") && edit_button.classList.contains('d-none')) {
		edit_box.classList.remove('d-none');
		edit_button.classList.remove('d-none');
	} else {
		edit_box.classList.add('d-none');
		edit_button.classList.add('d-none');
	}

	edit_button.addEventListener('click', () => {
		fetch(`/edit/${id}`, {
			method: 'PUT',
			body: JSON.stringify({
				post: edit_box.value
			})
		})
		.then(function() {
			edit_box.classList.add('d-none');
			edit_button.classList.add('d-none');
			document.querySelector(`#post-${id}`).innerHTML = edit_box.value;
		});
	});

	edit_box.value = "";
}

function like(id) {
	let like_button = document.querySelector(`#like-button-${id}`);
	let like_count = document.querySelector(`#like-count-${id}`);
	let btn_class = ["far", "fas"]

	console.log(like_count);
	fetch(`/like/${id}`)
	.then(response => response.json())
	.then(response => {
		like_count.innerHTML = response.likes;
		like_button.classList.remove(...btn_class)
		let class_to_add = (response.liked) ? 'far' : 'fas';
		like_button.classList.add(class_to_add)
	});
}