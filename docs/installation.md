# 環境構築

## 前提事項
鳴子が動作するリージョンが東京リージョンであること（リージョンを変更する場合は事前に[リージョンの変更について](#region)を参照してください）
鳴子とDBが接続可能であること（RDSを使用する場合はRDS側のセキュリティグループの設定をしてください）

## 1.CodeStar

AWSのCodeStarからDjango用の環境を作成します。  
画像のようにPython（Django）のAWS Elastic Beanstalkが選ばれていることを確認してください。  
![143883](img/build_env_1.png)

プロジェクト名は好きな名前を設定できます。  
リポジトリは好きな方を選ぶことができます。  
![143874](img/build_env_2.png)

ここで実際にアプリケーションが動くEC2のインスタンスタイプやVPC、サブネットを設定できます。（後から設定しなおすことも可能です）  
プロジェクトを作成するを押してしばらくしたら作成完了です。  
![143875](img/build_env_3.png)

CodeStarではダッシュボードから作成したアプリケーションの管理をすることができます。  
作成完了後にはエンドポイントが割り当てられるのでアクセスできるかどうか確認します。  
この時点ではCodeStarが自動的に作成した画面が表示されます。  
![143876](img/build_env_4.png)

##  2.設定値の作成

鳴子ではアプリケーションで使用する設定値をAWSのSystemManagerにあるパラメータストアで管理しています。  
鳴子を作成したリージョンと**同じリージョン**でパラメータストアにパラメータを作成してください。  

![143880](img/build_env_10.png)

設定値は以下のものがあります。  

| キー | 説明 |
| ------------- | ------------- |
| DEBUG  | デバッグ用 TrueまたはFalseを指定します |
| SES_ADDRESS  | SESで使用する送信用アドレス  |
| SES_REGION | 使用するSESのリージョン バージニア北部であれば「us-east-1」と設定します |
| LOG_GROUP | アプリケーションログの出力先となるCloudWatch Logsのロググループ名 |
|SNS_TOPIC_NAME  | 通知機能用のSNSトピック名 「NARUKO_NOTIFY」を設定してください。 |
| NOTIFY_TEXT_MESSAGE | 監視機能で送信される通知メールの本文を設定します※ |
| NOTIFY_TEXT_SUBJECT | 監視機能で送信される通知メールの件名を設定します |
| EVENT_SNS_TOPIC_ARN | スケジュール機能用のSNSトピックARN 「arn:aws:sns:{鳴子を利用するリージョン}:{鳴子を利用するAWSアカウントのID}:NARUKO_SCHEDULE」を設定します。 |
| DB_ENGINE | [Djangoのドキュメント](https://docs.djangoproject.com/ja/2.1/ref/settings/#engine) を参考に使用するDBのエンジンを設定します|
| DB_NAME | 使用するDBの名前を設定します（あらかじめ用意したDBをご利用ください） |
| DB_HOST | 使用するDBの接続先を設定します |
| DB_USER | 使用するDBのユーザー名を設定します |
| DB_PASSWORD | 使用するDBのパスワードを設定します |

※NOTIFY_TEXT_MESSAGEには以下の文字列({}を含む)を含めることで検知したアラートの詳細情報を記載することができます。  
　各文字列は監視検知の際に提供されるデータに対応しておりそれらを好きなものだけ組み合わせて自由に本文を定義することができます。  
　改行が必要な場合は「\n」で改行させることができます。  

| 文字列 | 説明 |
| ---- | ---- |
| {timestamp} | アラートを検知した時間 |
| {aws_name} | アラートを上げたリソースが所属するAWSアカウントの名前 |
| {aws_account_id} | アラートを上げたリソースが所属するAWSアカウントのID |
| {region} | アラートを上げたリソースが所属するリージョンの日本語名 |
| {service} | アラートを上げたリソースのサービス  EC2、RDS、ELB |
| {resource_id} | アラートを上げたリソースの識別子  EC2: インスタンスID  RDS: インスタンス識別子  ELB: ロードバランサー名 |
| {metrics} | アラート対象の監視項目 |
| {level} | アラートのレベル |

```
例：「鳴子からの監視検知のお知らせ\n\n{timestamp}に{aws_name}:{aws_account_id}の{region}における{service}:{resource_id}の{metrics}が{level}状態になりました」  
↓
鳴子からの監視検知のお知らせ


2018年12月01日 10時12分34秒にname:123456789012の東京リージョンにおけるEC2:i-xxxxxxxxxxxxxのネットワーク送信量が危険状態になりました
```

## 3.SES設定

鳴子ではAWSのSESを使用してメールを送信しています。  
SESでは初期状態では登録したメールアドレスでしか送受信を行うことができないため、[ドキュメント](https://docs.aws.amazon.com/ja_jp/ses/latest/DeveloperGuide/request-production-access.html)を参考にメールの受信はどのメールアドレスでも行えるように設定します。  
  
また、[ドキュメント](https://docs.aws.amazon.com/ja_jp/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html)を参考に送信用のメールアドレスを設定します。  
ここで設定するメールアドレスは設定値の「SES_ADDRESS」と同じメールアドレスにしてください。  

## 4.Iamロールの設定

鳴子ではプログラム内で様々なAWSサービスを利用しています。  
本手順に従って動作環境を構築している場合、「CodeStarWorker-{CodeStarのプロジェクト名}-EB」ロールに適切な権限を割り当てる必要があります。  
  
IAMから鳴子用のポリシーを作成します。  
ポリシーには以下のjsonを設定してください。  

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "events:DescribeRule",
                "tag:GetResources",
                "events:PutRule",
                "sns:CreateTopic",
                "sns:ListTopics",
                "ssm:GetParameters",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "sns:AddPermission",
                "events:PutTargets",
                "events:DeleteRule",
                "ses:SendEmail",
                "sts:AssumeRole",
                "logs:CreateLogStream",
                "cloudwatch:DescribeAlarms",
                "events:ListRules",
                "events:RemoveTargets",
                "sns:ConfirmSubscription"
            ],
            "Resource": "*"
        }
    ]
}
```

![143877](img/build_env_5.png)

名前と説明を入力してポリシーを作成します。  

![143878](img/build_env_6.png)

「CodeStarWorker-{CodeStarのプロジェクト名}-EB」に作成したポリシーをアタッチします。  

![143879](img/build_env_7.png)

## 5.ソースコードの反映

CodeStarで作成されたリポジトリのmasterブランチに鳴子のソースコードをpushします。  
CodeStar上でアプリケーションの反映が完了したことが確認出来たらエンドポイントにアクセスします。  
以下のようなログイン画面が表示されることを確認します。  

![143879](img/build_env_8.png)

## 6.動作確認

ログイン画面で  
メールアドレスに「admin@admin.com」  
パスワードに「Passw0rd!」  
と入力してログインボタンを押下します。  
  
ダッシュボードが表示されたら構築完了です。  
お疲れさまでした。  

![143879](img/build_env_9.png)


## 初期データについて

ElasticBeanstalkを利用した環境では毎デプロイ時に自動的に初期データが投入されます。  
そのため編集された初期データはデプロイ時に初期のデータに戻ります。  
編集した初期データを使い続けたい場合は以下のファイルを編集してください。  

[initial_data.json](https://github.com/crosspower/exam-pj/blob/master/backend/fixtures/initial_data.json)

## リージョンの変更について<a name="region"></a>

鳴子を利用されるリージョンを変更したい場合、以下のファイルを編集する必要があります。  

[base.py](https://github.com/crosspower/exam-pj/blob/master/config/settings/base.py): 15行目  

```
NARUKO_REGION = "ap-northeast-1"
```