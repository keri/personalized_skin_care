alert("Hi Keri - root js");

function testFunction( someString ) {
	var product = someString.shift();
	someString.push(product);
	// var price =  product['price'] ;
	// alert( product.price );
	// // document.write(product)
	return(product);

};



function init_clicks(){
	var mbtn = $('#btn-moisturizer')[0];
	mbtn.onclick = function(){
		product = testFunction(jmoisturizers)
		var title = document.getElementById("title")
		title.innerHTML = product.title
		var concern = $('#concern')[0].innerText
		alert(concern)

	};

};

