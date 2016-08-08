#!groovy

node {
    stage 'Build'
    checkout scm

    // Store the short commit id for use tagging images
    sh 'git rev-parse --short HEAD > GIT_SHA'
    gitSha = readFile('GIT_SHA').trim()

    sh "make docker DOCKER_TAG=${gitSha}"
    img = docker.image "hypothesis/hypothesis:${gitSha}"

    stage 'Test'

    elasticsearch = docker.image('nickstenning/elasticsearch-icu').run('-P')
    elasticsearchHost = sh(
        script: "echo http://\$(facter ipaddress_eth0):\$(docker port ${elasticsearch.id} 9200 | cut -d: -f2)",
        returnStdout: true
    ).trim()

    postgres = docker.image('postgres:9.4').run('-P -e POSTGRES_DB=htest')
    databaseUrl = sh(
        script: "echo postgresql://postgres@\$(facter ipaddress_eth0):\$(docker port ${postgres.id} 5432 | cut -d: -f2)/htest",
        returnStdout: true
    ).trim()

    redis = docker.image('redis').run('-P')
    redisHost = sh(
        script: "facter ipaddress_eth0", 
        returnStdout: true
    ).trim()
    redisPort = sh(
        script: "docker port ${redis.id} 6379 | cut -d: -f2", 
        returnStdout: true
    ).trim()

    try {
        // Run our Python tests inside the built container
        img.inside("-u root " +
                   "-e REDIS_HOST=${redisHost} " +
                   "-e REDIS_PORT=${redisPort} " +
                   "-e ELASTICSEARCH_HOST=${elasticsearchHost} " +
                   "-e TEST_DATABASE_URL=${databaseUrl}") {
            sh 'pip install -q tox'
            sh 'cd /var/lib/hypothesis && tox -r -e py27,functional'
        }
    } finally {
        redis.stop()
        postgres.stop()
        elasticsearch.stop()
    }

    // We only push the image to the Docker Hub if we're on master
    if (env.BRANCH_NAME != 'master') {
        return
    }
    stage 'Push'
    docker.withRegistry('', 'docker-hub-build') {
        img.push('auto')
    }
}
