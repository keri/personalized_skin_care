alert("Hi Keri - root js");

//$("#basket_price").value = "monkey breath"
 // import Products from "./products"

function testFunction( someString ) {
	var product = someString.shift()
	someString.unshift(product)
	var price =  product['price'] ;
	alert( product.price );
	document.write(product)
	return(product);

}



function init_clicks(){
	var mbtn = $('#btn-moisturizer')[0];
	mbtn.onclick = function(){
		alert("was clicked");
	};

}

// function getProduct( productList ) {
// 	$('#basket_concerns')[0].innerText = testFunction(productList)


// }
