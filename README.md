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
> !cloudfront list
E2W8XGZOTST0FT: example3.com
.
.
```

Create new distribution

```
> !cloudfront create example.com
Start creating new distribution example.com
Call `!cloudfront info E2W8XGZOTST0FT` to check invaliation status
```

Show info of distribution

```
> !cloudfront info E2W8XGZOTST0FT
Distribution: E2W8XGZOTST0FT
- comment: example3.com
- status: Deployed
- endpoint: d20kwhdbksw9zv.cloudfront.net
```

Invalidate cache of distribution

```
!cloudfront invalidate DISTRIBUTION_ID
```
