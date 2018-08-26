require 'json'
require 'csv'
require 'open-uri'
require 'active_support/all'
require 'nokogiri'
require 'twitter'
require './config.rb'

client = Twitter::REST::Client.new do |config|
  config.consumer_key = $consumer_key
  config.consumer_secret = $consumer_secret
  config.access_token = $access_token
  config.access_token_secret = $access_token_secret
end

USERS = [19040580, 914080998689607680, 913532586521116672, 907193396049182720, 
  920664872786059264, 899858978418642944, 904767529398157314, 892028249340915712,
  884907632426971136, 892808605170245632, 2853641871, 912696400571486208]

def get_transfer_tweets(client)
  transfer_data = JSON.parse(File.read('transfer.json')) rescue {}
  data = transfer_data['tweets'] || {}

  USERS.each do |u| 
    client.user_timeline(u).each do |tweet|
      tweet_data = (data[tweet.id.to_s] || {}).merge(tweet.attrs.with_indifferent_access)
      comments = (tweet_data['comments'] || [])
      comments.append(main_text)
      tweet_data['comments'] = comments.uniq.compact
      tweet_data['floor'] ||= post.css('.hashPermalink').text.gsub('#', '')
      tweet_data['link'] ||= link
      tweet_data['text'] = tweet.full_text
      tweet_data['in_reply_to'] ||= client.status(tweet.in_reply_to_status_id).attrs rescue nil
      data[tweet.id.to_s] = tweet_data
    end
  end
  File.open('transfer.json', 'w') do |f|
    f.write(transfer_data.to_json)
  end

end

get_transfer_tweets(client)
