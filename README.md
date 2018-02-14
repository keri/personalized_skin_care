# Customizing Product Recommendations Based on Skin Type/Concerns and Budget
## Business Understanding
There are overwhelming choices for skin products. Not only are the several product *categories* to choose from such as moisturizers, serum, mask, peel, there are thousands of products *within* each category. An amazon search for dry skin products returns 60,000 results. Add in one or two more skin concerns and it becomes impossible to find the right product for a users particular skin type with a quick search. I wanted to solve this problem and built a model that recommends products to users based on their top three skin concerns and budget. The model is deployed on aws. [Visit the website here](https://razzbeauty.com/) 


## Data Understanding
Reviews, title, image, and ingredients were scraped from amazon for two categories: moisturizer and serum. I limited the number of reviews for each product to 350 and modeled using reviews that had a rating of 4 and above.

![Ratings Distribution](/images/review_distribution.png)


All data is stored in a postresql instance on AWS.

## Modeling
1) Combined the reviews for each product, tokenized and fitted a Tf-idf Vectorizer using 400 words.
2) This matrix was factored using the sklearn NMF using 20 latent features -- >
  - The 20 X 400 matrix was then mapped back to the Tf-idf vector, which was used to pull out the top twenty words into 20         different clusters.
  - These clusters were rated for each area of concern providing a customized 20 X 16 matrix.
  - The dot product of this and the second NMF matrix was taken resulting in the final recommendation values.


## Skin Recommnedation Web App
The values for each concern are normalized using the number of ratings for each product, with review # / 350. A rating of 5 for a product with only one review does not have the same weight as a 5 rating for a product with 350 reviews.

The recommendations are sorted for each concern separately and the top three are displayed. There are two product categories, with three concerns, hence, there are 18 products displayed for each search.

![Home Page](/images/home_page.png)
![Product Page](/images/products.png)

## Evaluation
It is an unsupervised model and therefore not possible to evaluate with loss metrics. However, it makes decent predictions based on user feedback on comparing with the concerns with labels on the product.

![Product Page](/data/resized_product.png)
