# errrbot-cloudfront

Errbot plugin for CloudFront(list and invaldate)

## Prerequirements

IAM user to access CloudFront(ACCESS ID and SECRET KEY)


## Installation

In errbot, run this command

```
!repos install https://github.com/attakei/errbot-cloudfront.git
```

## Usage

List current distributions

```
!cloudfront list
```

Invalidate cache of distribution

```
!cloudfront invalidate DISTRIBUTION_ID
```
